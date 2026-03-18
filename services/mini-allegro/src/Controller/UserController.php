<?php

namespace App\Controller;

use App\Entity\User;
use App\Enum\UserRole;
use Psr\Log\LoggerInterface;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

#[Route('/users')]
class UserController extends AbstractController
{
    public function __construct(
        private readonly LoggerInterface $logger,
    ) {}

    #[Route('/', methods: ['GET'])]
    public function index(): JsonResponse
    {
        $users = [
            new User('jan.kowalski@example.com', 'Jan', 'Kowalski', [UserRole::CUSTOMER]),
            new User('anna.nowak@example.com', 'Anna', 'Nowak', [UserRole::SELLER]),
            new User('piotr.wisniewski@example.com', 'Piotr', 'Wiśniewski', [UserRole::CUSTOMER, UserRole::SELLER]),
        ];

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
}
