<?php

namespace App\Controller;

use App\Entity\User;
use App\Enum\UserRole;
use App\Repository\UserRepository;
use Doctrine\ORM\EntityManagerInterface;
use Psr\Log\LoggerInterface;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

#[Route('/users')]
class UserController extends AbstractController
{
    public function __construct(
        private readonly LoggerInterface $logger,
        private readonly UserRepository $userRepository,
    ) {}

    #[Route('', methods: ['GET'])]
    #[Route('/', methods: ['GET'])]
    public function index(): JsonResponse
    {
        $users = $this->userRepository->findAll();

        $responsePayload = array_map(fn(User $user) => $user->toArray(), $users);

        $rolesHistogram = [
            UserRole::CUSTOMER->value => 0,
            UserRole::SELLER->value => 0,
        ];

        foreach ($users as $user) {
            foreach ($user->getRoles() as $role) {
                $rolesHistogram[$role->value]++;
            }
        }

        $this->logger->info('Users fetched', [
            'endpoint' => '/users',
            'results_count' => count($responsePayload),
            'roles_histogram' => $rolesHistogram,
        ]);

        return $this->json(
            $responsePayload,
            Response::HTTP_OK,
        );
    }

    #[Route('', methods: ['POST'])]
    #[Route('/', methods: ['POST'])]
    public function create(Request $request, EntityManagerInterface $em): JsonResponse
    {
        $body = json_decode($request->getContent(), true);
        if (!is_array($body)) {
            return new JsonResponse(['error' => 'Invalid JSON payload'], Response::HTTP_BAD_REQUEST);
        }

        $email = $body['email'] ?? null;
        $firstName = $body['firstName'] ?? null;
        $lastName = $body['lastName'] ?? null;
        $rolesInput = $body['roles'] ?? [UserRole::CUSTOMER->value];

        if (!is_string($email) || trim($email) === '') {
            return new JsonResponse(['error' => 'Email is required'], Response::HTTP_BAD_REQUEST);
        }

        if (!is_string($firstName) || trim($firstName) === '') {
            return new JsonResponse(['error' => 'First name is required'], Response::HTTP_BAD_REQUEST);
        }

        if (!is_string($lastName) || trim($lastName) === '') {
            return new JsonResponse(['error' => 'Last name is required'], Response::HTTP_BAD_REQUEST);
        }

        if (!is_array($rolesInput) || $rolesInput === []) {
            return new JsonResponse(['error' => 'Roles must be a non-empty array'], Response::HTTP_BAD_REQUEST);
        }

        $roles = [];
        foreach ($rolesInput as $roleValue) {
            if (!is_string($roleValue)) {
                return new JsonResponse(['error' => 'Role values must be strings'], Response::HTTP_BAD_REQUEST);
            }

            $role = UserRole::tryFrom($roleValue);
            if ($role === null) {
                return new JsonResponse(['error' => sprintf('Invalid role: %s', $roleValue)], Response::HTTP_BAD_REQUEST);
            }

            if (!in_array($role, $roles, true)) {
                $roles[] = $role;
            }
        }

        $user = new User(trim($email), trim($firstName), trim($lastName), $roles);

        $em->persist($user);
        $em->flush();

        return new JsonResponse($user->toArray(), Response::HTTP_CREATED);
    }
}
