<?php

namespace App\Controller;

use App\Entity\User;
use App\Enum\UserRole;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

#[Route('/users')]
class UserController extends AbstractController
{
    #[Route('/', methods: ['GET'])]
    public function index(): JsonResponse
    {
        $users = [
            new User('jan.kowalski@example.com', 'Jan', 'Kowalski', [UserRole::CUSTOMER]),
            new User('anna.nowak@example.com', 'Anna', 'Nowak', [UserRole::SELLER]),
            new User('piotr.wisniewski@example.com', 'Piotr', 'Wiśniewski', [UserRole::CUSTOMER, UserRole::SELLER]),
        ];

        return $this->json(
            array_map(fn(User $user) => $user->toArray(), $users),
            Response::HTTP_OK,
        );
    }
}
