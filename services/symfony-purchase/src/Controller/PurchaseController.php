<?php

namespace App\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\DependencyInjection\Attribute\Autowire;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;
use Symfony\Contracts\HttpClient\HttpClientInterface;

#[Route('/purchases', name: 'app_purchase_')]
final class PurchaseController
{
    public function __construct(
        private readonly HttpClientInterface $httpClient,
        #[Autowire('%env(resolve:PURCHASE_SERVICE_URL)%')]
        private readonly string $serviceUrl,
    ) {
    }

    #[Route('', name: 'index', methods: ['GET'])]
    public function index(): JsonResponse
    {
        try {
            $upstreamResponse = $this->httpClient->request(
                'GET',
                rtrim($this->serviceUrl, '/') . '/purchases',
                ['timeout' => 5.0]
            );

            $content = $upstreamResponse->getContent();
            return new JsonResponse($content, Response::HTTP_OK, ['Content-Type' => 'application/json'], true);
        } catch (\Throwable) {
            return new JsonResponse(['error' => 'Upstream service unavailable'], Response::HTTP_BAD_GATEWAY);
        }
    }
}
