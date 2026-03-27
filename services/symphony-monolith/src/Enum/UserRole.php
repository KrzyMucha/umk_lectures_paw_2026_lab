<?php

namespace App\Enum;

enum UserRole: string
{
    case CUSTOMER = 'ROLE_CUSTOMER';
    case SELLER   = 'ROLE_SELLER';
}
