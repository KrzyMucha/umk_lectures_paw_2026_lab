<?php

namespace App\Controller;

use App\Entity\Product;
use App\Repository\ProductRepository;
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
    public function index(ProductRepository $productRepo): JsonResponse
    {
        $products = $productRepo->findAll();

        $data = array_map(static fn(Product $product) => $product->toArray(), $products);

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

        $name = $body['name'] ?? null;
        $description = $body['description'] ?? null;
        $price = $body['price'] ?? null;

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
}
