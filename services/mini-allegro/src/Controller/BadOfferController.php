<?php

namespace App\Controller;

use Psr\Log\LoggerInterface;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

class BadOfferController extends AbstractController
{
    public function __construct(
        private readonly LoggerInterface $logger,
    ) {}

    #[Route('/bad_offer', methods: ['GET'])]
    public function __invoke(): JsonResponse
    {
        $this->logger->error('Bad offer request', [
            'endpoint' => '/bad_offer',
            'reason' => 'invalid_offer_identifier',
            'offer_id' => 'invalid',
        ]);

        return $this->json(
            ['error' => 'Bad offer'],
            Response::HTTP_BAD_REQUEST
        );
    }
}