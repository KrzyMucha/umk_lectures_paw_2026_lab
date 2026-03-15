<?php

namespace App\Controller;

use App\Entity\Product;
use App\Entity\ProductReview;
use App\Repository\ProductRepository;
use App\Repository\ProductReviewRepository;
use Doctrine\ORM\EntityManagerInterface;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

#[Route('/products')]
class ProductController extends AbstractController
{
    #[Route('', methods: ['GET'])]
    public function index(ProductRepository $productRepo, ProductReviewRepository $reviewRepo): JsonResponse
    {
        $products = $productRepo->findAll();

        $data = array_map(function (Product $product) use ($reviewRepo) {
            $result = $product->toArray();
            $result['averageRating'] = round($reviewRepo->getAverageRating($product->getId()), 2);
            $result['reviewCount'] = $reviewRepo->countByProduct($product->getId());
            return $result;
        }, $products);

        return new JsonResponse($data);
    }

    #[Route('/{id}', methods: ['GET'])]
    public function show(int $id, ProductRepository $productRepo, ProductReviewRepository $reviewRepo): JsonResponse
    {
        $product = $productRepo->find($id);
        if (!$product) {
            return new JsonResponse(['error' => 'Product not found'], Response::HTTP_NOT_FOUND);
        }

        $data = $product->toArray();
        $data['averageRating'] = round($reviewRepo->getAverageRating($id), 2);
        $data['reviewCount'] = $reviewRepo->countByProduct($id);

        return new JsonResponse($data);
    }

    #[Route('/{id}/reviews', methods: ['GET'])]
    public function reviews(int $id, ProductRepository $productRepo, ProductReviewRepository $reviewRepo): JsonResponse
    {
        $product = $productRepo->find($id);
        if (!$product) {
            return new JsonResponse(['error' => 'Product not found'], Response::HTTP_NOT_FOUND);
        }

        $reviews = $reviewRepo->findByProduct($id);
        $data = array_map(fn(ProductReview $r) => $r->toArray(), $reviews);

        return new JsonResponse($data);
    }

    #[Route('/{id}/reviews', methods: ['POST'])]
    public function addReview(int $id, Request $request, ProductRepository $productRepo, EntityManagerInterface $em): JsonResponse
    {
        $product = $productRepo->find($id);
        if (!$product) {
            return new JsonResponse(['error' => 'Product not found'], Response::HTTP_NOT_FOUND);
        }

        $body = json_decode($request->getContent(), true);
        $rating = $body['rating'] ?? null;
        $comment = $body['comment'] ?? null;
        $authorName = $body['authorName'] ?? null;

        if (!is_int($rating) || $rating < 1 || $rating > 5) {
            return new JsonResponse(['error' => 'Rating must be an integer between 1 and 5'], Response::HTTP_BAD_REQUEST);
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
}
