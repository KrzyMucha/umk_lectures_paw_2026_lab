<?php

declare(strict_types=1);

namespace App\Controller;

use App\Entity\Offer;
use App\Repository\OfferRepository;
use Doctrine\ORM\EntityManagerInterface;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\Routing\Attribute\Route;

#[Route('/offers')]
class OfferController extends AbstractController
{
    #[Route('', name: 'offer_index', methods: ['GET'])]
    public function index(OfferRepository $offerRepository): JsonResponse
    {
        $offers = array_map(
            fn (Offer $offer): array => $this->serializeOffer($offer),
            $offerRepository->findBy([], ['id' => 'DESC'])
        );

        return $this->json($offers);
    }

    #[Route('/{id}', name: 'offer_show', methods: ['GET'])]
    public function show(?Offer $offer): JsonResponse
    {
        if ($offer === null) {
            return $this->json(['message' => 'Offer not found'], JsonResponse::HTTP_NOT_FOUND);
        }

        return $this->json($this->serializeOffer($offer));
    }

    #[Route('', name: 'offer_create', methods: ['POST'])]
    public function create(Request $request, EntityManagerInterface $entityManager): JsonResponse
    {
        $payload = $this->decodePayload($request);
        if ($payload instanceof JsonResponse) {
            return $payload;
        }

        $validationError = $this->validatePayload($payload);
        if ($validationError instanceof JsonResponse) {
            return $validationError;
        }

        $offer = (new Offer())
            ->setTitle(trim($payload['title']))
            ->setDescription(trim($payload['description']))
            ->setPrice((string) $payload['price']);

        $entityManager->persist($offer);
        $entityManager->flush();

        return $this->json($this->serializeOffer($offer), JsonResponse::HTTP_CREATED);
    }

    #[Route('/{id}', name: 'offer_update', methods: ['PUT'])]
    public function update(?Offer $offer, Request $request, EntityManagerInterface $entityManager): JsonResponse
    {
        if ($offer === null) {
            return $this->json(['message' => 'Offer not found'], JsonResponse::HTTP_NOT_FOUND);
        }

        $payload = $this->decodePayload($request);
        if ($payload instanceof JsonResponse) {
            return $payload;
        }

        $validationError = $this->validatePayload($payload);
        if ($validationError instanceof JsonResponse) {
            return $validationError;
        }

        $offer
            ->setTitle(trim($payload['title']))
            ->setDescription(trim($payload['description']))
            ->setPrice((string) $payload['price']);

        $entityManager->flush();

        return $this->json($this->serializeOffer($offer));
    }

    #[Route('/{id}', name: 'offer_delete', methods: ['DELETE'])]
    public function delete(?Offer $offer, EntityManagerInterface $entityManager): JsonResponse
    {
        if ($offer === null) {
            return $this->json(['message' => 'Offer not found'], JsonResponse::HTTP_NOT_FOUND);
        }

        $entityManager->remove($offer);
        $entityManager->flush();

        return $this->json(null, JsonResponse::HTTP_NO_CONTENT);
    }

    private function decodePayload(Request $request): array|JsonResponse
    {
        try {
            $payload = $request->toArray();
        } catch (\JsonException) {
            return $this->json(['message' => 'Invalid JSON payload'], JsonResponse::HTTP_BAD_REQUEST);
        }

        return $payload;
    }

    private function validatePayload(array $payload): ?JsonResponse
    {
        foreach (['title', 'description', 'price'] as $requiredField) {
            if (!array_key_exists($requiredField, $payload)) {
                return $this->json([
                    'message' => sprintf('Field "%s" is required', $requiredField),
                ], JsonResponse::HTTP_BAD_REQUEST);
            }
        }

        if (!is_numeric($payload['price'])) {
            return $this->json(['message' => 'Field "price" must be numeric'], JsonResponse::HTTP_BAD_REQUEST);
        }

        return null;
    }

    private function serializeOffer(Offer $offer): array
    {
        return [
            'id' => $offer->getId(),
            'title' => $offer->getTitle(),
            'description' => $offer->getDescription(),
            'price' => $offer->getPrice(),
            'createdAt' => $offer->getCreatedAt()?->format(DATE_ATOM),
            'updatedAt' => $offer->getUpdatedAt()?->format(DATE_ATOM),
        ];
    }
}
