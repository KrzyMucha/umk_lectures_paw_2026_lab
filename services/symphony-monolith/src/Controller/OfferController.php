<?php

namespace App\Controller;

use Psr\Log\LoggerInterface;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

#[Route('/offers')]
class OfferController extends AbstractController
{
    private string $offersServiceUrl;

    public function __construct(
        private readonly LoggerInterface $logger,
    ) {
        $this->offersServiceUrl = rtrim($_ENV['OFFERS_SERVICE_URL'] ?? 'http://offers-service:8082', '/');
    }

    #[Route('', methods: ['GET'])]
    #[Route('/', methods: ['GET'])]
    public function index(): JsonResponse
    {
        return $this->proxy('GET', '/offers');
    }

    #[Route('-super', name: 'offers_super', methods: ['GET'])]
    public function super(): JsonResponse
    {
        return $this->proxy('GET', '/offers-super');
    }

    #[Route('-super', name: 'offers_super_patch', methods: ['PATCH'])]
    public function assignSuperSeller(Request $request): JsonResponse
    {
        return $this->proxy('PATCH', '/offers-super', $request->getContent());
    }

    #[Route('', methods: ['POST'])]
    #[Route('/', methods: ['POST'])]
    public function create(Request $request): JsonResponse
    {
        return $this->proxy('POST', '/offers', $request->getContent());
    }

    private function proxy(string $method, string $path, ?string $body = null): JsonResponse
    {
        $url = $this->offersServiceUrl . $path;

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
            $this->logger->error('Failed to proxy request to offers-service', [
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
