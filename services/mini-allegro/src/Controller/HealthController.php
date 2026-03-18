<?php

namespace App\Controller;

use Psr\Log\LoggerInterface;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

#[Route('/health')]
class HealthController extends AbstractController
{
    public function __construct(
        private readonly LoggerInterface $logger,
    ) {}

    #[Route('', methods: ['GET'])]
    #[Route('/', methods: ['GET'])]
    public function index(): JsonResponse
    {
        $this->logger->info('Health check', [
            'endpoint' => '/health',
            'status' => 'ok',
        ]);

        return $this->json(['status' => 'ok'], Response::HTTP_OK);
    }

    #[Route('/error', methods: ['GET'])]
    public function testError(): JsonResponse
    {
        $this->logger->error('Forced test error for alert policy verification', [
            'endpoint' => '/health/error',
            'test_error' => true,
            'purpose' => 'Cloud Monitoring alert trigger test',
        ]);

        return $this->json(
            ['error' => 'Test error endpoint'],
            Response::HTTP_INTERNAL_SERVER_ERROR
        );
    }
}
