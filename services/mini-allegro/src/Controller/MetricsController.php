<?php

namespace App\Controller;

use App\Service\MetricsCollector;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

#[Route('/metrics')]
class MetricsController extends AbstractController
{
    public function __construct(
        private readonly MetricsCollector $metrics,
    ) {}

    #[Route('', methods: ['GET'])]
    #[Route('/', methods: ['GET'])]
    public function index(): JsonResponse
    {
        $raw = $this->metrics->getAll();

        // Parse the flat cache keys back into structured data
        $endpoints = [];
        foreach ($raw as $key => $count) {
            // key format: http_requests_{endpoint}_{statusCode}
            if (preg_match('/^http_requests_(.+)_(\d{3})$/', $key, $m)) {
                $endpoint = '/' . str_replace('_', '/', $m[1]);
                $status = (int) $m[2];
                $endpoints[$endpoint][$status] = $count;
            }
        }

        $totalRequests = array_sum($raw);

        return $this->json([
            'total_requests' => $totalRequests,
            'endpoints' => $endpoints,
        ], Response::HTTP_OK);
    }
}
