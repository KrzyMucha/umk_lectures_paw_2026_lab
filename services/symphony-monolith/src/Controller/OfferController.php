<?php

namespace App\Controller;

use App\Entity\Offer;
use App\Entity\SuperSeller;
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

    #[Route('-super', name: 'offers_super', methods: ['GET'])]
    public function super(OfferRepository $offerRepo): JsonResponse
    {
        $offers = $offerRepo->createQueryBuilder('o')
            ->where('o.superSeller IS NOT NULL')
            ->getQuery()
            ->getResult();

        $responsePayload = array_map(fn(Offer $offer) => $offer->toArray(), $offers);

        return $this->json($responsePayload, Response::HTTP_OK);
    }

    #[Route('-super', name: 'offers_super_patch', methods: ['PATCH'])]
    public function assignSuperSeller(Request $request, EntityManagerInterface $em): JsonResponse
    {
        $body = json_decode($request->getContent(), true);
        if (!is_array($body)) {
            return new JsonResponse(['error' => 'Invalid JSON payload'], Response::HTTP_BAD_REQUEST);
        }

        $offerId = $body['offerId'] ?? null;
        $superSellerId = $body['superSellerId'] ?? null;

        if (!is_int($offerId) || !is_int($superSellerId)) {
            return new JsonResponse(['error' => 'offerId and superSellerId are required (int)'], Response::HTTP_BAD_REQUEST);
        }

        $offer = $em->find(Offer::class, $offerId);
        if (!$offer) {
            return new JsonResponse(['error' => 'Offer not found'], Response::HTTP_NOT_FOUND);
        }

        $superSeller = $em->find(SuperSeller::class, $superSellerId);
        if (!$superSeller) {
            return new JsonResponse(['error' => 'SuperSeller not found'], Response::HTTP_NOT_FOUND);
        }

        $offer->setSuperSeller($superSeller);
        $em->flush();

        return new JsonResponse($offer->toArray(), Response::HTTP_OK);
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
