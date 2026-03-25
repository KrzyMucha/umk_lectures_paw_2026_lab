<?php

namespace App\Entity;

use App\Repository\OfferRepository;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity(repositoryClass: OfferRepository::class)]
#[ORM\Table(name: 'offers')]
class Offer
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    private ?int $id = null;

    #[ORM\Column(length: 255)]
    private string $title;

    #[ORM\Column(type: 'text')]
    private string $description;

    #[ORM\Column(type: 'decimal', precision: 10, scale: 2)]
    private string $price;

    #[ORM\Column]
    private \DateTimeImmutable $createdAt;

    public function __construct(string $title, string $description, float $price)
    {
        $this->title       = $title;
        $this->description = $description;
        $this->price       = (string) $price;
        $this->createdAt   = new \DateTimeImmutable();
    }

    public function getId(): ?int { return $this->id; }
    public function getTitle(): string { return $this->title; }
    public function getDescription(): string { return $this->description; }
    public function getPrice(): float { return (float) $this->price; }
    public function getCreatedAt(): \DateTimeImmutable { return $this->createdAt; }

    public function setTitle(string $title): void { $this->title = $title; }
    public function setDescription(string $description): void { $this->description = $description; }
    public function setPrice(float $price): void { $this->price = (string) $price; }

    public function toArray(): array
    {
        return [
            'id'          => $this->id,
            'title'       => $this->title,
            'description' => $this->description,
            'price'       => $this->getPrice(),
            'createdAt'   => $this->createdAt->format(\DateTimeInterface::ATOM),
        ];
    }
}
