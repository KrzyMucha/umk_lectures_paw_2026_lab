<?php

namespace App\Entity;

use App\Repository\PurchaseRepository;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity(repositoryClass: PurchaseRepository::class)]
class Purchase
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    private ?int $id = null;

    #[ORM\Column]
    private int $userId;

    #[ORM\Column]
    private int $offerId;

    #[ORM\Column]
    private int $quantity;

    #[ORM\Column(type: 'float')]
    private float $pricePerUnit;

    #[ORM\Column(length: 32)]
    private string $status;

    #[ORM\ManyToOne]
    private ?SuperSeller $superSeller = null;

    public function __construct(
        int $userId,
        int $offerId,
        int $quantity,
        float $pricePerUnit,
        string $status = 'completed', // pending, completed, cancelled
    ) {
        $this->userId = $userId;
        $this->offerId = $offerId;
        $this->quantity = $quantity;
        $this->pricePerUnit = $pricePerUnit;
        $this->status = $status;
    }

    public function getId(): ?int { return $this->id; }

    public function getUserId(): int { return $this->userId; }
    public function setUserId(int $userId): self { $this->userId = $userId; return $this; }

    public function getOfferId(): int { return $this->offerId; }
    public function setOfferId(int $offerId): self { $this->offerId = $offerId; return $this; }

    public function getQuantity(): int { return $this->quantity; }
    public function setQuantity(int $quantity): self { $this->quantity = $quantity; return $this; }

    public function getPricePerUnit(): float { return $this->pricePerUnit; }
    public function setPricePerUnit(float $pricePerUnit): self { $this->pricePerUnit = $pricePerUnit; return $this; }

    public function getStatus(): string { return $this->status; }
    public function setStatus(string $status): self { $this->status = $status; return $this; }

    public function getSuperSeller(): ?SuperSeller { return $this->superSeller; }
    public function setSuperSeller(?SuperSeller $superSeller): self { $this->superSeller = $superSeller; return $this; }

    public function getTotalPrice(): float { return $this->quantity * $this->pricePerUnit; }

    public function toArray(): array
    {
        return [
            'id' => $this->id ?? 0,
            'userId' => $this->userId,
            'offerId' => $this->offerId,
            'quantity' => $this->quantity,
            'pricePerUnit' => $this->pricePerUnit,
            'totalPrice' => $this->getTotalPrice(),
            'status' => $this->status,
        ];
    }
}
