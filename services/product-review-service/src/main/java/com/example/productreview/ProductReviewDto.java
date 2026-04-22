package com.example.productreview;

public record ProductReviewDto(
        Integer id,
        Integer productId,
        Integer rating,
        String comment,
        String authorName,
        Integer offerId,
        String createdAt
) {}
