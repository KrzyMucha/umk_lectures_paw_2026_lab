<?php

declare(strict_types=1);

namespace App\Controller;

use App\Entity\Offer;
use App\Repository\OfferRepository;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;
use Symfony\Component\Validator\Validator\ValidatorInterface;

#[Route('/offers', name: 'offer_')]
class OfferController extends AbstractController
{
    public function __construct(
        private readonly OfferRepository  $offerRepository,
        private readonly ValidatorInterface $validator,
    ) {}

    /**
     * GET /offers - list all offers
     */
    #[Route('', name: 'list', methods: ['GET'])]
    public function list(): JsonResponse
    {
        $offers = $this->offerRepository->findAll();

        return $this->json(
            array_map(static fn(Offer $o) => $o->toArray(), $offers)
        );
    }

    /**
     * GET /offers/{id} - get single offer
     */
    #[Route('/{id}', name: 'show', methods: ['GET'], requirements: ['id' => '\d+'])]
    public function show(int $id): JsonResponse
    {
        $offer = $this->offerRepository->find($id);

        if (!$offer) {
            return $this->json(['error' => 'Offer not found.'], Response::HTTP_NOT_FOUND);
        }

        return $this->json($offer->toArray());
    }

    /**
     * POST /offers - create new offer
     * Body: { "title": "...", "description": "...", "price": "99.99" }
     */
    #[Route('', name: 'create', methods: ['POST'])]
    public function create(Request $request): JsonResponse
    {
        $data = $this->decodeJson($request);

        if ($data === null) {
            return $this->json(['error' => 'Invalid JSON body.'], Response::HTTP_BAD_REQUEST);
        }

        $offer = new Offer();
        $offer->setTitle($data['title'] ?? '');
        $offer->setDescription($data['description'] ?? null);
        $offer->setPrice((string) ($data['price'] ?? '0'));

        $violations = $this->validator->validate($offer);
        if (count($violations) > 0) {
            return $this->json($this->formatViolations($violations), Response::HTTP_UNPROCESSABLE_ENTITY);
        }

        $this->offerRepository->save($offer);

        return $this->json($offer->toArray(), Response::HTTP_CREATED);
    }

    /**
     * PUT /offers/{id} - update offer
     * Body (all fields optional): { "title": "...", "description": "...", "price": "..." }
     */
    #[Route('/{id}', name: 'update', methods: ['PUT'], requirements: ['id' => '\d+'])]
    public function update(int $id, Request $request): JsonResponse
    {
        $offer = $this->offerRepository->find($id);

        if (!$offer) {
            return $this->json(['error' => 'Offer not found.'], Response::HTTP_NOT_FOUND);
        }

        $data = $this->decodeJson($request);

        if ($data === null) {
            return $this->json(['error' => 'Invalid JSON body.'], Response::HTTP_BAD_REQUEST);
        }

        if (array_key_exists('title', $data)) {
            $offer->setTitle($data['title']);
        }
        if (array_key_exists('description', $data)) {
            $offer->setDescription($data['description']);
        }
        if (array_key_exists('price', $data)) {
            $offer->setPrice((string) $data['price']);
        }

        $violations = $this->validator->validate($offer);
        if (count($violations) > 0) {
            return $this->json($this->formatViolations($violations), Response::HTTP_UNPROCESSABLE_ENTITY);
        }

        $this->offerRepository->save($offer);

        return $this->json($offer->toArray());
    }

    /**
     * DELETE /offers/{id} - delete offer
     */
    #[Route('/{id}', name: 'delete', methods: ['DELETE'], requirements: ['id' => '\d+'])]
    public function delete(int $id): JsonResponse
    {
        $offer = $this->offerRepository->find($id);

        if (!$offer) {
            return $this->json(['error' => 'Offer not found.'], Response::HTTP_NOT_FOUND);
        }

        $this->offerRepository->remove($offer);

        return $this->json(null, Response::HTTP_NO_CONTENT);
    }

    // -------------------------------------------------------------------------

    private function decodeJson(Request $request): ?array
    {
        $content = $request->getContent();

        if (empty($content)) {
            return [];
        }

        $data = json_decode($content, true);

        if (json_last_error() !== JSON_ERROR_NONE) {
            return null;
        }

        return $data;
    }

    private function formatViolations(\Symfony\Component\Validator\ConstraintViolationListInterface $violations): array
    {
        $errors = [];
        foreach ($violations as $violation) {
            $errors[] = [
                'field'   => $violation->getPropertyPath(),
                'message' => $violation->getMessage(),
            ];
        }

        return ['errors' => $errors];
    }
}
