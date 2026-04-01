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

#[Route('/purchases')]
class PurchaseController extends AbstractController
{
    public function __construct(
        private readonly LoggerInterface $logger,
        private readonly PurchaseRepository $purchaseRepository,
    ) {}

    #[Route('', methods: ['GET'])]
    #[Route('/', methods: ['GET'])]
    public function index(): JsonResponse
    {
        $purchases = $this->purchaseRepository->findAll();

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

    #[Route('', methods: ['POST'])]
    #[Route('/', methods: ['POST'])]
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
