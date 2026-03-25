<?php

namespace App\Controller;

use App\Entity\Offer;
use App\Repository\OfferRepository;
use Psr\Log\LoggerInterface;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

#[Route('/offers')]
class OfferController extends AbstractController
{
    public function __construct(
        private readonly OfferRepository $offerRepository,
        private readonly LoggerInterface $logger,
    ) {}

    #[Route('', methods: ['GET'])]
    #[Route('/', methods: ['GET'])]
    public function index(): JsonResponse
    {
        $offers = $this->offerRepository->findAll();
        $payload = array_map(fn(Offer $offer) => $offer->toArray(), $offers);

        $this->logger->info('Offers fetched', [
            'endpoint'      => '/offers',
            'results_count' => count($payload),
        ]);

        return $this->json($payload, Response::HTTP_OK);
    }

    #[Route('', methods: ['POST'])]
    #[Route('/', methods: ['POST'])]
    public function create(Request $request): JsonResponse
    {
        $data = json_decode($request->getContent(), true);

        if (!isset($data['title'], $data['description'], $data['price'])) {
            return $this->json(
                ['error' => 'Fields required: title, description, price'],
                Response::HTTP_UNPROCESSABLE_ENTITY,
            );
        }

        if (!is_numeric($data['price']) || $data['price'] <= 0) {
            return $this->json(
                ['error' => 'price must be a positive number'],
                Response::HTTP_UNPROCESSABLE_ENTITY,
            );
        }

        $offer = new Offer(
            trim($data['title']),
            trim($data['description']),
            (float) $data['price'],
        );

        $this->offerRepository->save($offer);

        $this->logger->info('Offer created', [
            'endpoint' => '/offers',
            'offer_id' => $offer->getId(),
        ]);

        return $this->json($offer->toArray(), Response::HTTP_CREATED);
    }
}
