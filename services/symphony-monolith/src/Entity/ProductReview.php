<?php

declare(strict_types=1);

namespace App\Entity;

use App\Repository\ProductReviewRepository;
use Doctrine\ORM\Mapping as ORM;
use App\Entity\Offer;

#[ORM\Entity(repositoryClass: ProductReviewRepository::class)]
class ProductReview
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    private ?int $id = null;

    #[ORM\ManyToOne(targetEntity: Product::class)]
    #[ORM\JoinColumn(nullable: false)]
    private ?Product $product = null;

    #[ORM\Column(type: 'smallint')]
    private int $rating;

    #[ORM\Column(type: 'text', nullable: true)]
    private ?string $comment = null;

    #[ORM\Column(type: 'string', length: 255, nullable: true)]
    private ?string $authorName = null;

    #[ORM\ManyToOne(targetEntity: Offer::class)]
    #[ORM\JoinColumn(nullable: true)]
    private ?Offer $offer = null;

    #[ORM\Column(type: 'datetime_immutable')]
    private \DateTimeImmutable $createdAt;

    public function __construct()
    {
        $this->createdAt = new \DateTimeImmutable();
    }

    public function getId(): ?int { return $this->id; }

    public function getProduct(): ?Product { return $this->product; }
    public function setProduct(?Product $product): self { $this->product = $product; return $this; }

    public function getRating(): int { return $this->rating; }
    public function setRating(int $rating): self { $this->rating = $rating; return $this; }

    public function getComment(): ?string { return $this->comment; }
    public function setComment(?string $comment): self { $this->comment = $comment; return $this; }

    public function getAuthorName(): ?string { return $this->authorName; }
    public function setAuthorName(?string $name): self { $this->authorName = $name; return $this; }

    public function getOffer(): ?Offer { return $this->offer; }
    public function setOffer(?Offer $offer): self { $this->offer = $offer; return $this; }

    public function getCreatedAt(): \DateTimeImmutable { return $this->createdAt; }

    public function toArray(): array
    {
        return [
            'id'         => $this->id,
            'productId'  => $this->product?->getId(),
            'rating'     => $this->rating,
            'comment'    => $this->comment,
            'authorName' => $this->authorName,
            'offerId'    => $this->offer?->getId(),
            'createdAt'  => $this->createdAt->format(\DateTimeInterface::ATOM),
        ];
    }
}
