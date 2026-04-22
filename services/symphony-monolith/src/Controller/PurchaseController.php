<?php

namespace App\Controller;

use App\Entity\Purchase;
use App\Repository\PurchaseRepository;
use Doctrine\ORM\EntityManagerInterface;
use Psr\Log\LoggerInterface;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;
use Symfony\Contracts\HttpClient\HttpClientInterface;

class PurchaseController extends AbstractController
{
    public function __construct(
        private readonly LoggerInterface $logger,
        private readonly PurchaseRepository $purchaseRepository,
        private readonly HttpClientInterface $httpClient,
    ) {}

    #[Route('/purchases', methods: ['GET'])]
    #[Route('/purchases/', methods: ['GET'])]
    public function index(): JsonResponse
    {
        $purchaseServiceUrl = rtrim((string) ($_ENV['PURCHASE_SERVICE_URL'] ?? $_SERVER['PURCHASE_SERVICE_URL'] ?? ''), '/');
        if ($purchaseServiceUrl === '') {
            return new JsonResponse([
                'error' => 'Purchase service unavailable',
                'details' => 'PURCHASE_SERVICE_URL is not configured',
            ], Response::HTTP_BAD_GATEWAY);
        }

        try {
            $response = $this->httpClient->request('GET', sprintf('%s/purchases', $purchaseServiceUrl), [
                'timeout' => 5,
            ]);

            $statusCode = $response->getStatusCode();
            $rawBody = $response->getContent(false);

            if ($statusCode >= 400) {
                return new JsonResponse([
                    'error' => 'Purchase service returned an error',
                    'statusCode' => $statusCode,
                ], Response::HTTP_BAD_GATEWAY);
            }

            $decoded = json_decode($rawBody, true);
            if (!is_array($decoded)) {
                return new JsonResponse([
                    'error' => 'Purchase service returned invalid payload',
                ], Response::HTTP_BAD_GATEWAY);
            }

            $responsePayload = $decoded;
        } catch (\Throwable $exception) {
            return new JsonResponse([
                'error' => 'Purchase service unavailable',
                'details' => $exception->getMessage(),
            ], Response::HTTP_BAD_GATEWAY);
        }

        // Aggregate stats for logging (no PII)
        $totalRevenue = array_reduce($responsePayload, fn($sum, $p) => $sum + ((float) ($p['totalPrice'] ?? 0)), 0.0);
        $statusCounts = [];
        foreach ($responsePayload as $p) {
            $status = (string) ($p['status'] ?? 'unknown');
            $statusCounts[$status] = ($statusCounts[$status] ?? 0) + 1;
        }

        $this->logger->info('Purchases fetched', [
            'endpoint' => '/purchases',
            'results_count' => count($responsePayload),
            'total_revenue' => $totalRevenue,
            'status_distribution' => $statusCounts,
            'source' => 'purchase-service',
        ]);

        return $this->json($responsePayload, Response::HTTP_OK);
    }

    #[Route('/purchases/offer/{offerId}', methods: ['GET'])]
    public function byOffer(int $offerId): JsonResponse
    {
        $filtered = $this->purchaseRepository->findBy(['offerId' => $offerId]);
        $responsePayload = array_map(fn(Purchase $p) => $p->toArray(), $filtered);

        $offerRevenue = array_reduce($filtered, fn($sum, $p) => $sum + $p->getTotalPrice(), 0);
        $totalUnits = array_reduce($filtered, fn($sum, $p) => $sum + $p->getQuantity(), 0);

        $this->logger->info('Purchases by offer fetched', [
            'endpoint' => '/purchases/offer/{offerId}',
            'offer_id' => $offerId,
            'results_count' => count($responsePayload),
            'offer_total_revenue' => $offerRevenue,
            'offer_total_units_sold' => $totalUnits,
        ]);

        return $this->json($responsePayload, Response::HTTP_OK);
    }

    #[Route('/purchases-super', methods: ['GET'])]
    #[Route('/purchases-super/', methods: ['GET'])]
    public function superPurchases(): JsonResponse
    {
        $purchases = $this->purchaseRepository
            ->createQueryBuilder('p')
            ->andWhere('p.superSeller IS NOT NULL')
            ->getQuery()
            ->getResult();

        $responsePayload = array_map(
            static fn(Purchase $purchase) => array_merge($purchase->toArray(), [
                'superSellerId' => $purchase->getSuperSeller()?->getId(),
            ]),
            $purchases
        );

        return $this->json($responsePayload, Response::HTTP_OK);
    }

    #[Route('/purchases', methods: ['POST'])]
    #[Route('/purchases/', methods: ['POST'])]
    public function create(Request $request, EntityManagerInterface $entityManager): JsonResponse
    {
        $payload = json_decode($request->getContent(), true);
        if (!is_array($payload)) {
            return $this->json(['error' => 'Invalid JSON payload'], Response::HTTP_BAD_REQUEST);
        }

        $userId = $payload['userId'] ?? null;
        $offerId = $payload['offerId'] ?? null;
        $quantity = $payload['quantity'] ?? null;
        $pricePerUnit = $payload['pricePerUnit'] ?? null;
        $status = $payload['status'] ?? 'completed';

        if (!is_numeric($userId) || !is_numeric($offerId) || !is_numeric($quantity) || !is_numeric($pricePerUnit) || !is_string($status)) {
            return $this->json(['error' => 'Fields userId, offerId, quantity, pricePerUnit, status are required'], Response::HTTP_BAD_REQUEST);
        }

        $purchase = new Purchase((int) $userId, (int) $offerId, (int) $quantity, (float) $pricePerUnit, trim($status));
        $entityManager->persist($purchase);
        $entityManager->flush();

        return $this->json($purchase->toArray(), Response::HTTP_CREATED);
    }
}
