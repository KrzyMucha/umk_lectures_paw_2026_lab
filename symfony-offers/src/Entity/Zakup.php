<?php

namespace App\Entity;

class Zakup
{
    public function __construct(
        private string $buyerName,
        private string $offerTitle,
        private int $quantity,
        private float $totalPrice,
        private \DateTimeImmutable $purchasedAt = new \DateTimeImmutable(),
    ) {}

    public function toArray(): array
    {
        return [
            'buyerName'   => $this->buyerName,
            'offerTitle'  => $this->offerTitle,
            'quantity'    => $this->quantity,
            'totalPrice'  => $this->totalPrice,
            'purchasedAt' => $this->purchasedAt->format(\DateTimeInterface::ATOM),
        ];
    }
}
