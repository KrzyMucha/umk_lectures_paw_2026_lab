<?php

namespace App\Entity;

class Purchase
{
    private ?int $id = null;

    public function __construct(
        private int $userId,
        private int $offerId,
        private int $quantity,
        private float $pricePerUnit,
        private string $status = 'completed', // pending, completed, cancelled
    ) {}

    public function getId(): ?int { return $this->id; }
    public function getUserId(): int { return $this->userId; }
    public function getOfferId(): int { return $this->offerId; }
    public function getQuantity(): int { return $this->quantity; }
    public function getPricePerUnit(): float { return $this->pricePerUnit; }
    public function getStatus(): string { return $this->status; }
    public function getTotalPrice(): float { return $this->quantity * $this->pricePerUnit; }

    public function toArray(): array
    {
        return [
            'id' => $this->id,
            'userId' => $this->userId,
            'offerId' => $this->offerId,
            'quantity' => $this->quantity,
            'pricePerUnit' => $this->pricePerUnit,
            'totalPrice' => $this->getTotalPrice(),
            'status' => $this->status,
        ];
    }
}
