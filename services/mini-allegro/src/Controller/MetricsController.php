<?php

namespace App\Controller;

use App\Service\MetricsCollector;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
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
    public function index(): Response
    {
        $lines = [];
        $lines[] = '# HELP http_requests_total Total number of HTTP requests';
        $lines[] = '# TYPE http_requests_total counter';

        foreach ($this->metrics->getAll() as $entry) {
            $endpoint   = addslashes($entry['endpoint']);
            $statusCode = $entry['status_code'];
            $count      = $entry['count'];

            $lines[] = sprintf(
                'http_requests_total{endpoint="%s",status_code="%d"} %d',
                $endpoint,
                $statusCode,
                $count,
            );
        }

        $lines[] = '';

        return new Response(
            implode("\n", $lines),
            Response::HTTP_OK,
            ['Content-Type' => 'text/plain; version=0.0.4; charset=utf-8'],
        );
    }
}
