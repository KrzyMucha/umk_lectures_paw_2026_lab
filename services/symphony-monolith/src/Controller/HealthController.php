<?php

namespace App\Controller;

use Psr\Log\LoggerInterface;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\DependencyInjection\Attribute\Autowire;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

#[Route('/health')]
class HealthController extends AbstractController
{
    public function __construct(
        private readonly LoggerInterface $logger,
        #[Autowire(env: 'APP_ENV')]
        private readonly string $appEnv,
    ) {}

    #[Route('', methods: ['GET'])]
    #[Route('/', methods: ['GET'])]
    public function index(): JsonResponse
    {
        $checks = $this->runChecks();
        $allOk = !in_array('error', array_column($checks, 'status'), true);
        $httpStatus = $allOk ? Response::HTTP_OK : Response::HTTP_SERVICE_UNAVAILABLE;

        $this->logger->info('Health check', [
            'endpoint' => '/health',
            'status' => $allOk ? 'ok' : 'degraded',
        ]);

        return $this->json([
            'status' => $allOk ? 'ok' : 'degraded',
            'checks' => $checks,
            'meta' => [
                'php_version' => PHP_VERSION,
                'env' => $this->appEnv,
                'timestamp' => (new \DateTimeImmutable())->format(\DateTimeInterface::ATOM),
            ],
        ], $httpStatus);
    }

    private function runChecks(): array
    {
        return [
            'php' => $this->checkPhp(),
            'disk' => $this->checkDisk(),
        ];
    }

    private function checkPhp(): array
    {
        $ok = version_compare(PHP_VERSION, '8.3.0', '>=');

        return [
            'status' => $ok ? 'ok' : 'error',
            'detail' => sprintf('PHP %s', PHP_VERSION),
        ];
    }

    private function checkDisk(): array
    {
        $free = disk_free_space('/');
        $total = disk_total_space('/');

        if ($free === false || $total === false || $total === 0.0) {
            return ['status' => 'error', 'detail' => 'Unable to read disk space'];
        }

        $usedPercent = (int) round(($total - $free) / $total * 100);
        $status = $usedPercent >= 95 ? 'error' : ($usedPercent >= 80 ? 'warn' : 'ok');

        return [
            'status' => $status,
            'detail' => sprintf('%d%% used (%s free)', $usedPercent, $this->formatBytes((int) $free)),
        ];
    }

    private function formatBytes(int $bytes): string
    {
        $units = ['B', 'KB', 'MB', 'GB'];
        $i = 0;
        while ($bytes >= 1024 && $i < count($units) - 1) {
            $bytes = (int) ($bytes / 1024);
            $i++;
        }

        return $bytes . ' ' . $units[$i];
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
