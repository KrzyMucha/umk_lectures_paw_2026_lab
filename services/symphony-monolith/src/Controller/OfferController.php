<?php

namespace App\Controller;

use App\Entity\Offer;
use App\Repository\OfferRepository;
use Doctrine\ORM\EntityManagerInterface;
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
        private readonly LoggerInterface $logger,
    ) {}

    #[Route('', methods: ['GET'])]
    #[Route('/', methods: ['GET'])]
    public function index(OfferRepository $offerRepo): JsonResponse
    {
        $offers = $offerRepo->findAll();
        $responsePayload = array_map(fn(Offer $offer) => $offer->toArray(), $offers);

        $this->logger->info('Offers fetched', [
            'endpoint' => '/offers',
            'results_count' => count($responsePayload),
        ]);

        return $this->json($responsePayload, Response::HTTP_OK);
    }

    #[Route('', methods: ['POST'])]
    #[Route('/', methods: ['POST'])]
    public function create(Request $request, EntityManagerInterface $em): JsonResponse
    {
        $body = json_decode($request->getContent(), true);
        if (!is_array($body)) {
            return new JsonResponse(['error' => 'Invalid JSON payload'], Response::HTTP_BAD_REQUEST);
        }

        $title = $body['title'] ?? null;
        $description = $body['description'] ?? null;
        $price = $body['price'] ?? null;

        if (!is_string($title) || trim($title) === '') {
            return new JsonResponse(['error' => 'Title is required'], Response::HTTP_BAD_REQUEST);
        }

        if (!is_null($description) && !is_string($description)) {
            return new JsonResponse(['error' => 'Description must be a string or null'], Response::HTTP_BAD_REQUEST);
        }

        if (!is_numeric($price)) {
            return new JsonResponse(['error' => 'Price must be numeric'], Response::HTTP_BAD_REQUEST);
        }

        $offer = new Offer(trim($title), $description, (float) $price);

        $em->persist($offer);
        $em->flush();

        return new JsonResponse($offer->toArray(), Response::HTTP_CREATED);
    }
}
