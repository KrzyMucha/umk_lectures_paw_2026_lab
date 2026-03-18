<?php

namespace App\Controller;

use App\Entity\Purchase;
use Psr\Log\LoggerInterface;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

#[Route('/purchases')]
class PurchaseController extends AbstractController
{
    public function __construct(
        private readonly LoggerInterface $logger,
    ) {}

    #[Route('', methods: ['GET'])]
    #[Route('/', methods: ['GET'])]
    public function index(): JsonResponse
    {
        // Mock data – w produkcji z bazy danych
        $purchases = [
            new Purchase(1, 1, 2, 4999.99, 'completed'),
            new Purchase(2, 2, 1, 12999.99, 'completed'),
            new Purchase(1, 2, 1, 12999.99, 'pending'),
            new Purchase(3, 1, 5, 4999.99, 'completed'),
        ];

        $responsePayload = array_map(fn(Purchase $purchase) => $purchase->toArray(), $purchases);

        // Aggregate stats for logging (no PII)
        $totalRevenue = array_reduce($purchases, fn($sum, $p) => $sum + $p->getTotalPrice(), 0);
        $statusCounts = [];
        foreach ($purchases as $p) {
            $status = $p->getStatus();
            $statusCounts[$status] = ($statusCounts[$status] ?? 0) + 1;
        }

        $this->logger->info('Purchases fetched', [
            'endpoint' => '/purchases',
            'results_count' => count($responsePayload),
            'total_revenue' => $totalRevenue,
            'status_distribution' => $statusCounts,
        ]);

        return $this->json($responsePayload, Response::HTTP_OK);
    }

    #[Route('/offer/{offerId}', methods: ['GET'])]
    public function byOffer(int $offerId): JsonResponse
    {
        // Mock data – w produkcji z bazy danych
        $allPurchases = [
            new Purchase(1, 1, 2, 4999.99, 'completed'),
            new Purchase(2, 2, 1, 12999.99, 'completed'),
            new Purchase(1, 2, 1, 12999.99, 'pending'),
            new Purchase(3, 1, 5, 4999.99, 'completed'),
        ];

        // Filter by offerId
        $filtered = array_filter($allPurchases, fn(Purchase $p) => $p->getOfferId() === $offerId);
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
}
