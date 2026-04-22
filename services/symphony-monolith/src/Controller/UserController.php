<?php

namespace App\Controller;

use Psr\Log\LoggerInterface;
use App\Service\UserServiceClient;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

class UserController extends AbstractController
{
    public function __construct(
        private readonly LoggerInterface $logger,
        private readonly UserServiceClient $userServiceClient,
    ) {}

    #[Route('/users', methods: ['GET'])]
    #[Route('/users/', methods: ['GET'])]
    public function index(): JsonResponse
    {
        $result = $this->userServiceClient->getUsers();

        $this->logger->info('Users fetched', [
            'endpoint' => '/users',
            'results_count' => is_array($result['payload']) ? count($result['payload']) : 0,
            'upstream_status' => $result['status'],
        ]);

        return $this->json(
            $result['payload'],
            $result['status'],
        );
    }

    #[Route('/users-super', methods: ['GET'])]
    #[Route('/users-super/', methods: ['GET'])]
    public function superUsers(): JsonResponse
    {
        $result = $this->userServiceClient->getSuperUsers();

        $this->logger->info('Super users fetched', [
            'endpoint' => '/users-super',
            'results_count' => is_array($result['payload']) ? count($result['payload']) : 0,
            'upstream_status' => $result['status'],
        ]);

        return $this->json(
            $result['payload'],
            $result['status'],
        );
    }

    #[Route('/users', methods: ['POST'])]
    #[Route('/users/', methods: ['POST'])]
    public function create(Request $request): JsonResponse
    {
        $result = $this->userServiceClient->createUser($request->getContent());

        return $this->json($result['payload'], $result['status']);
    }

    #[Route('/user/{userId}', methods: ['GET'])]
    public function show(int $userId): JsonResponse
    {
        $result = $this->userServiceClient->getUserById($userId);

        return $this->json($result['payload'], $result['status']);
    }
}
