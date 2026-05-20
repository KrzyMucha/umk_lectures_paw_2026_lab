<?php

namespace App\Controller;

use App\Service\OffersService;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\Routing\Attribute\Route;

#[Route('/offers')]
class OfferController extends AbstractController
{
    public function __construct(
        private readonly OffersService $offersService,
    ) {}

    #[Route('', methods: ['GET'])]
    #[Route('/', methods: ['GET'])]
    public function index(): JsonResponse
    {
        return $this->offersService->getOffers();
    }

    #[Route('-super', name: 'offers_super', methods: ['GET'])]
    public function super(): JsonResponse
    {
        return $this->offersService->getSuperOffers();
    }

    #[Route('-super', name: 'offers_super_patch', methods: ['PATCH'])]
    public function assignSuperSeller(Request $request): JsonResponse
    {
        return $this->offersService->assignSuperSeller($request->getContent());
    }

    #[Route('', methods: ['POST'])]
    #[Route('/', methods: ['POST'])]
    public function create(Request $request): JsonResponse
    {
        return $this->offersService->createOffer($request->getContent());
    }
}
