<?php

declare(strict_types=1);

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
    #[Route('/', methods: ['GET'])]
    public function index(ProductRepository $productRepo, ProductReviewRepository $reviewRepo): JsonResponse
    {
        $products = $productRepo->findAll();

        $data = array_map(static function (Product $product) use ($reviewRepo) {
            $result = $product->toArray();
            $result['averageRating'] = round($reviewRepo->getAverageRating($product->getId()), 2);
            $result['reviewCount']   = $reviewRepo->countByProduct($product->getId());
            return $result;
        }, $products);

        return new JsonResponse($data);
    }

    #[Route('', methods: ['POST'])]
    #[Route('/', methods: ['POST'])]
    public function create(Request $request, EntityManagerInterface $em): JsonResponse
    {
        $body = json_decode($request->getContent(), true);
        if (!is_array($body)) {
            return new JsonResponse(['error' => 'Invalid JSON payload'], Response::HTTP_BAD_REQUEST);
        }

        $name        = $body['name'] ?? null;
        $description = $body['description'] ?? null;
        $price       = $body['price'] ?? null;

        if (!is_string($name) || trim($name) === '') {
            return new JsonResponse(['error' => 'Name is required'], Response::HTTP_BAD_REQUEST);
        }

        if (!is_null($description) && !is_string($description)) {
            return new JsonResponse(['error' => 'Description must be a string or null'], Response::HTTP_BAD_REQUEST);
        }

        if (!is_numeric($price)) {
            return new JsonResponse(['error' => 'Price must be numeric'], Response::HTTP_BAD_REQUEST);
        }

        $product = new Product();
        $product->setName(trim($name));
        $product->setDescription($description);
        $product->setPrice((float) $price);

        $em->persist($product);
        $em->flush();

        return new JsonResponse($product->toArray(), Response::HTTP_CREATED);
    }

    #[Route('/{id}/reviews', methods: ['GET'])]
    public function reviews(int $id, ProductRepository $productRepo, ProductReviewRepository $reviewRepo): JsonResponse
    {
        $product = $productRepo->find($id);
        if (!$product) {
            return new JsonResponse(['error' => 'Product not found'], Response::HTTP_NOT_FOUND);
        }

        $data = array_map(
            static fn(ProductReview $r) => $r->toArray(),
            $reviewRepo->findByProduct($id)
        );

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
        if (!is_array($body)) {
            return new JsonResponse(['error' => 'Invalid JSON payload'], Response::HTTP_BAD_REQUEST);
        }

        $rating     = $body['rating'] ?? null;
        $comment    = $body['comment'] ?? null;
        $authorName = $body['authorName'] ?? null;

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
}
