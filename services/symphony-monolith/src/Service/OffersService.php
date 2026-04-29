<?php

namespace App\Service;

use Psr\Log\LoggerInterface;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Response;

class OffersService
{
    private string $baseUrl;

    public function __construct(
        private readonly LoggerInterface $logger,
    ) {
        $this->baseUrl = rtrim($_ENV['OFFERS_SERVICE_URL'] ?? 'http://offers-service:8082', '/');
    }

    public function getOffers(): JsonResponse
    {
        return $this->request('GET', '/offers');
    }

    public function createOffer(string $body): JsonResponse
    {
        return $this->request('POST', '/offers', $body);
    }

    public function getSuperOffers(): JsonResponse
    {
        return $this->request('GET', '/offers-super');
    }

    public function assignSuperSeller(string $body): JsonResponse
    {
        return $this->request('PATCH', '/offers-super', $body);
    }

    private function request(string $method, string $path, ?string $body = null): JsonResponse
    {
        $url = $this->baseUrl . $path;

        $opts = [
            'http' => [
                'method' => $method,
                'header' => "Content-Type: application/json\r\nAccept: application/json\r\n",
                'ignore_errors' => true,
                'timeout' => 10,
            ],
        ];

        if ($body !== null) {
            $opts['http']['content'] = $body;
        }

        $context = stream_context_create($opts);
        $response = @file_get_contents($url, false, $context);

        if ($response === false) {
            $this->logger->error('Failed to reach offers-service', [
                'url' => $url,
                'method' => $method,
            ]);
            return new JsonResponse(
                ['error' => 'Offers service unavailable'],
                Response::HTTP_BAD_GATEWAY
            );
        }

        $statusCode = $this->extractStatusCode($http_response_header ?? []);
        $data = json_decode($response, true);

        return new JsonResponse($data, $statusCode);
    }

    private function extractStatusCode(array $headers): int
    {
        foreach ($headers as $header) {
            if (preg_match('/^HTTP\/\S+\s+(\d{3})/', $header, $matches)) {
                return (int) $matches[1];
            }
        }
        return Response::HTTP_BAD_GATEWAY;
    }
}
