<?php

declare(strict_types=1);

namespace App\Entity;

class Offer
{
    public function __construct(
        private string $title,
        private string $description,
        private float $price
    ) {}

    public function toArray(): array
    {
        return [
            'title' => $this->title,
            'description' => $this->description,
            'price' => $this->price,
        ];
    }
}
