<?php

namespace App\Controller;

use App\Entity\SuperSeller;
use App\Repository\SuperSellerRepository;
use Doctrine\ORM\EntityManagerInterface;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

#[Route('/super-sellers')]
class SuperSellerController extends AbstractController
{
    #[Route('', methods: ['GET'])]
    #[Route('/', methods: ['GET'])]
    public function index(SuperSellerRepository $repo): JsonResponse
    {
        $sellers = $repo->findAll();
        $payload = array_map(fn(SuperSeller $s) => [
            'id' => $s->getId(),
            'name' => $s->getName(),
            'isActive' => $s->isActive(),
            'createdAt' => $s->getCreatedAt()->format('Y-m-d H:i:s'),
        ], $sellers);

        return $this->json($payload, Response::HTTP_OK);
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
        if (!is_string($name) || trim($name) === '') {
            return new JsonResponse(['error' => 'Name is required'], Response::HTTP_BAD_REQUEST);
        }

        $seller = new SuperSeller();
        $seller->setName(trim($name));

        if (isset($body['isActive'])) {
            $seller->setIsActive((bool) $body['isActive']);
        }

        $em->persist($seller);
        $em->flush();

        return new JsonResponse([
            'id' => $seller->getId(),
            'name' => $seller->getName(),
            'isActive' => $seller->isActive(),
            'createdAt' => $seller->getCreatedAt()->format('Y-m-d H:i:s'),
        ], Response::HTTP_CREATED);
    }
}
