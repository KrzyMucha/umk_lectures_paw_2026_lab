<?php

namespace App\Controller;

use App\Entity\Offer;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

#[Route('/offers')]
class OfferController extends AbstractController
{
    #[Route('', methods: ['GET'])]
    public function index(): JsonResponse
    {
        $offers = [
            new Offer('iPhone 15', 'Nowy, zafoliowany', 4999.99),
            new Offer('MacBook Pro', '16 cali, M3', 12999.99),
        ];

        return $this->json(
            array_map(fn(Offer $offer) => $offer->toArray(), $offers),
            Response::HTTP_OK,
        );
    }
}
