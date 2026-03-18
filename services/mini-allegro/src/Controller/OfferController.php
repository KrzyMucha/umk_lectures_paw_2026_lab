<?php

namespace App\Controller;

use App\Entity\Offer;
use Psr\Log\LoggerInterface;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

#[Route('/offers')]
class OfferController extends AbstractController
{
    public function __construct(
        private readonly LoggerInterface $logger,
    ) {}

    #[Route('', methods: ['GET'])]
    #[Route('/', methods: ['GET'])]
    public function index(): JsonResponse
    {
        $offers = [
            new Offer('iPhone 15', 'Nowy, zafoliowany', 4999.99),
            new Offer('MacBook Pro', '16 cali, M3', 12999.99),
        ];

        $responsePayload = array_map(fn(Offer $offer) => $offer->toArray(), $offers);

        $this->logger->info('Offers fetched', [
            'endpoint' => '/offers',
            'results_count' => count($responsePayload),
            'offer_ids' => array_values(array_filter(array_map(fn(Offer $offer) => $offer->getId(), $offers))),
        ]);

        return $this->json(
            $responsePayload,
            Response::HTTP_OK,
        );
    }
}
