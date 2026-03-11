<?php

namespace App\Entity;

use App\Enum\UserRole;

class User
{
    private ?int $id = null;

    /** @var UserRole[] */
    private array $roles;

    public function __construct(
        private string $email,
        private string $firstName,
        private string $lastName,
        array $roles = [UserRole::CUSTOMER],
    ) {
        $this->roles = $roles;
    }

    public function getId(): ?int { return $this->id; }
    public function getEmail(): string { return $this->email; }
    public function getFirstName(): string { return $this->firstName; }
    public function getLastName(): string { return $this->lastName; }
    public function getFullName(): string { return $this->firstName . ' ' . $this->lastName; }

    /** @return UserRole[] */
    public function getRoles(): array { return $this->roles; }

    public function isCustomer(): bool
    {
        return in_array(UserRole::CUSTOMER, $this->roles, true);
    }

    public function isSeller(): bool
    {
        return in_array(UserRole::SELLER, $this->roles, true);
    }

    public function addRole(UserRole $role): void
    {
        if (!in_array($role, $this->roles, true)) {
            $this->roles[] = $role;
        }
    }

    public function removeRole(UserRole $role): void
    {
        $this->roles = array_values(
            array_filter($this->roles, fn(UserRole $r) => $r !== $role)
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
            'roles'     => array_map(fn(UserRole $r) => $r->value, $this->roles),
            'isCustomer' => $this->isCustomer(),
            'isSeller'   => $this->isSeller(),
        ];
    }
}
