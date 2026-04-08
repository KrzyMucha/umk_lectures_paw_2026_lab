<?php

namespace App\Entity;

use App\Enum\UserRole;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity]
#[ORM\Table(name: '`user`')]
class User
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    private ?int $id = null;

    /** @var string[] */
    #[ORM\Column(type: 'simple_array')]
    private array $roles;

    #[ORM\ManyToOne(targetEntity: SuperSeller::class)]
    #[ORM\JoinColumn(nullable: true)]
    private ?SuperSeller $superSeller = null;

    public function __construct(
        #[ORM\Column(length: 255, unique: true)]
        private string $email,
        #[ORM\Column(length: 255)]
        private string $firstName,
        #[ORM\Column(length: 255)]
        private string $lastName,
        array $roles = [UserRole::CUSTOMER->value],
    ) {
        $this->setRoles($roles);
    }

    public function getId(): ?int { return $this->id; }
    public function getEmail(): string { return $this->email; }
    public function setEmail(string $email): self { $this->email = $email; return $this; }

    public function getFirstName(): string { return $this->firstName; }
    public function setFirstName(string $firstName): self { $this->firstName = $firstName; return $this; }

    public function getLastName(): string { return $this->lastName; }
    public function setLastName(string $lastName): self { $this->lastName = $lastName; return $this; }

    public function getSuperSeller(): ?SuperSeller { return $this->superSeller; }
    public function setSuperSeller(?SuperSeller $superSeller): self { $this->superSeller = $superSeller; return $this; }

    public function getFullName(): string { return $this->firstName . ' ' . $this->lastName; }

    /** @return UserRole[] */
    public function getRoles(): array
    {
        return array_values(array_filter(
            array_map(static fn(string $roleValue) => UserRole::tryFrom($roleValue), $this->roles)
        ));
    }

    /** @param array<UserRole|string> $roles */
    public function setRoles(array $roles): self
    {
        $normalized = [];

        foreach ($roles as $role) {
            if ($role instanceof UserRole) {
                $value = $role->value;
            } elseif (is_string($role) && UserRole::tryFrom($role) !== null) {
                $value = $role;
            } else {
                continue;
            }

            if (!in_array($value, $normalized, true)) {
                $normalized[] = $value;
            }
        }

        $this->roles = $normalized;

        return $this;
    }

    public function isCustomer(): bool
    {
        return in_array(UserRole::CUSTOMER->value, $this->roles, true);
    }

    public function isSeller(): bool
    {
        return in_array(UserRole::SELLER->value, $this->roles, true);
    }

    public function addRole(UserRole $role): void
    {
        if (!in_array($role->value, $this->roles, true)) {
            $this->roles[] = $role->value;
        }
    }

    public function removeRole(UserRole $role): void
    {
        $this->roles = array_values(
            array_filter($this->roles, fn(string $r) => $r !== $role->value)
        );
    }

    public function toArray(): array
    {
        return [
            'id'        => $this->id,
            'email'     => $this->email,
            'firstName' => $this->firstName,
            'lastName'  => $this->lastName,
            'fullName'  => $this->getFullName(),
            'roles'     => array_map(fn(UserRole $r) => $r->value, $this->getRoles()),
            'isCustomer' => $this->isCustomer(),
            'isSeller'   => $this->isSeller(),
        ];
    }
}
