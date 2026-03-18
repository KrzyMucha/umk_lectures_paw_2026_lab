<?php

declare(strict_types=1);

namespace App\Repository;

use App\Entity\Offer;
use Doctrine\Bundle\DoctrineBundle\Repository\ServiceEntityRepository;
use Doctrine\Persistence\ManagerRegistry;

/**
 * @extends ServiceEntityRepository<Offer>
 */
class OfferRepository extends ServiceEntityRepository
{
    public function __construct(ManagerRegistry $registry)
    {
        parent::__construct($registry, Offer::class);
    }

    public function save(Offer $offer, bool $flush = true): void
    {
        $this->getEntityManager()->persist($offer);

        if ($flush) {
            $this->getEntityManager()->flush();
        }
    }

    public function remove(Offer $offer, bool $flush = true): void
    {
        $this->getEntityManager()->remove($offer);

        if ($flush) {
            $this->getEntityManager()->flush();
        }
    }
}
