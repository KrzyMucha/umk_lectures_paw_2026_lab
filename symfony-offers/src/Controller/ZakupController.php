<?php

namespace App\Controller;

use App\Entity\Zakup;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\Routing\Attribute\Route;

class ZakupController extends AbstractController
{
    #[Route('/zakupy', methods: ['GET'])]
    public function index(): JsonResponse
    {
        $zakupy = [
            new Zakup('Jan Kowalski', 'iPhone 15', 1, 4999.99),
            new Zakup('Anna Nowak', 'MacBook Pro', 2, 25999.98),
        ];

        return $this->json(
            array_map(fn($z) => $z->toArray(), $zakupy)
        );
    }
}
