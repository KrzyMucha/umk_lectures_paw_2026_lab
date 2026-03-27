<?php

namespace App\Repository;

use App\Entity\ProductReview;
use Doctrine\Bundle\DoctrineBundle\Repository\ServiceEntityRepository;
use Doctrine\Persistence\ManagerRegistry;

class ProductReviewRepository extends ServiceEntityRepository
{
    public function __construct(ManagerRegistry $registry)
    {
        parent::__construct($registry, ProductReview::class);
    }

    public function findByProduct(int $productId): array
    {
        return $this->createQueryBuilder('r')
            ->where('r.product = :productId')
            ->setParameter('productId', $productId)
            ->orderBy('r.createdAt', 'DESC')
            ->getQuery()
            ->getResult();
    }

    public function getAverageRating(int $productId): float
    {
        return (float) $this->createQueryBuilder('r')
            ->select('AVG(r.rating)')
            ->where('r.product = :productId')
            ->setParameter('productId', $productId)
            ->getQuery()
            ->getSingleScalarResult();
    }

    public function countByProduct(int $productId): int
    {
        return (int) $this->createQueryBuilder('r')
            ->select('COUNT(r.id)')
            ->where('r.product = :productId')
            ->setParameter('productId', $productId)
            ->getQuery()
            ->getSingleScalarResult();
    }
}