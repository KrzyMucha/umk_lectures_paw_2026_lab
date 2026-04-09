<?php

declare(strict_types=1);

namespace App\Controller;

use App\Entity\ProductReview;
use App\Repository\OfferRepository;
use App\Repository\ProductRepository;
use App\Repository\ProductReviewRepository;
use Doctrine\ORM\EntityManagerInterface;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

class ProductReviewController extends AbstractController
{
    #[Route('/product-reviews', methods: ['GET'])]
    #[Route('/product-reviews/', methods: ['GET'])]
    public function index(ProductReviewRepository $reviewRepo): JsonResponse
    {
        $data = array_map(
            static fn(ProductReview $r) => $r->toArray(),
            $reviewRepo->findAll()
        );

        return new JsonResponse($data);
    }

    #[Route('/product-reviews', methods: ['POST'])]
    #[Route('/product-reviews/', methods: ['POST'])]
    public function create(Request $request, ProductRepository $productRepo, EntityManagerInterface $em): JsonResponse
    {
        $body = json_decode($request->getContent(), true);
        if (!is_array($body)) {
            return new JsonResponse(['error' => 'Invalid JSON payload'], Response::HTTP_BAD_REQUEST);
        }

        $productId  = $body['productId'] ?? null;
        $rating     = $body['rating'] ?? null;
        $comment    = $body['comment'] ?? null;
        $authorName = $body['authorName'] ?? null;

        if (!is_int($productId)) {
            return new JsonResponse(['error' => 'productId must be an integer'], Response::HTTP_BAD_REQUEST);
        }

        $product = $productRepo->find($productId);
        if (!$product) {
            return new JsonResponse(['error' => 'Product not found'], Response::HTTP_NOT_FOUND);
        }

        if (!is_int($rating) || $rating < 1 || $rating > 5) {
            return new JsonResponse(['error' => 'Rating must be an integer between 1 and 5'], Response::HTTP_BAD_REQUEST);
        }

        if (!is_null($comment) && !is_string($comment)) {
            return new JsonResponse(['error' => 'Comment must be a string or null'], Response::HTTP_BAD_REQUEST);
        }

        if (!is_null($authorName) && !is_string($authorName)) {
            return new JsonResponse(['error' => 'AuthorName must be a string or null'], Response::HTTP_BAD_REQUEST);
        }

        $review = new ProductReview();
        $review->setProduct($product);
        $review->setRating($rating);
        $review->setComment($comment);
        $review->setAuthorName($authorName);

        $em->persist($review);
        $em->flush();

        return new JsonResponse($review->toArray(), Response::HTTP_CREATED);
    }

    #[Route('/reviews-super', methods: ['GET'])]
    public function superIndex(ProductReviewRepository $reviewRepo): JsonResponse
    {
        $reviews = $reviewRepo->createQueryBuilder('r')
            ->join('r.offer', 'o')
            ->join('o.superSeller', 's')
            ->getQuery()
            ->getResult();

        $data = array_map(static fn(ProductReview $r) => $r->toArray(), $reviews);

        return new JsonResponse($data);
    }

    #[Route('/reviews-super', methods: ['POST'])]
    public function superCreate(Request $request, ProductRepository $productRepo, OfferRepository $offerRepo, EntityManagerInterface $em): JsonResponse
    {
        $body = json_decode($request->getContent(), true);
        if (!is_array($body)) {
            return new JsonResponse(['error' => 'Invalid JSON payload'], Response::HTTP_BAD_REQUEST);
        }

        $productId  = $body['productId'] ?? null;
        $rating     = $body['rating'] ?? null;
        $comment    = $body['comment'] ?? null;
        $authorName = $body['authorName'] ?? null;
        $offerId    = $body['offerId'] ?? null;

        if (!is_int($productId)) {
            return new JsonResponse(['error' => 'productId must be an integer'], Response::HTTP_BAD_REQUEST);
        }

        $product = $productRepo->find($productId);
        if (!$product) {
            return new JsonResponse(['error' => 'Product not found'], Response::HTTP_NOT_FOUND);
        }

        if (!is_int($rating) || $rating < 1 || $rating > 5) {
            return new JsonResponse(['error' => 'Rating must be an integer between 1 and 5'], Response::HTTP_BAD_REQUEST);
        }

        if (!is_int($offerId)) {
            return new JsonResponse(['error' => 'offerId must be an integer'], Response::HTTP_BAD_REQUEST);
        }

        $offer = $offerRepo->find($offerId);
        if (!$offer) {
            return new JsonResponse(['error' => 'Offer not found'], Response::HTTP_NOT_FOUND);
        }

        if ($offer->getSuperSeller() === null) {
            return new JsonResponse(['error' => 'Offer does not belong to a SuperSeller'], Response::HTTP_BAD_REQUEST);
        }

        $review = new ProductReview();
        $review->setProduct($product);
        $review->setRating($rating);
        $review->setComment($comment);
        $review->setAuthorName($authorName);
        $review->setOffer($offer);

        $em->persist($review);
        $em->flush();

        return new JsonResponse($review->toArray(), Response::HTTP_CREATED);
    }
}
