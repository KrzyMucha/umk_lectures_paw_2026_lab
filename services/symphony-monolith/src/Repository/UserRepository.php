<?php

namespace App\Repository;

use App\Entity\User;
use Doctrine\Bundle\DoctrineBundle\Repository\ServiceEntityRepository;
use Doctrine\Persistence\ManagerRegistry;

class UserRepository extends ServiceEntityRepository
{
    public function __construct(ManagerRegistry $registry)
    {
        parent::__construct($registry, User::class);
    }

    /** @return User[] */
    public function findUsersWithSuperSeller(): array
    {
        return $this->createQueryBuilder('u')
            ->andWhere('u.superSeller IS NOT NULL')
            ->getQuery()
            ->getResult();
    }
}
