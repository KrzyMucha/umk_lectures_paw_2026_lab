<?php

declare(strict_types=1);

namespace App\Controller;

use App\Entity\Offer;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\Routing\Attribute\Route;

class OfferController extends AbstractController
{
    #[Route('/offers', name: 'offer_index', methods: ['GET'])]
    public function index(): JsonResponse
    {
        $offers = [
            new Offer('iPhone 15', 'Nowy, zafoliowany', 4999.99),
            new Offer('MacBook Pro', '16 cali, M3', 12999.99),
        ];

        return $this->json(
            array_map(fn(Offer $o) => $o->toArray(), $offers)
        );
    }
}
