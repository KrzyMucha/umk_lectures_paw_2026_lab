package com.example.productreview;

import java.time.OffsetDateTime;
import java.time.format.DateTimeFormatter;

public record ProductReviewDto(
        Integer id,
        Integer productId,
        Integer rating,
        String comment,
        String authorName,
        Integer offerId,
        String createdAt
) {
    static ProductReviewDto from(ProductReview r) {
        return new ProductReviewDto(
                r.getId(),
                r.getProductId(),
                r.getRating(),
                r.getComment(),
                r.getAuthorName(),
                r.getOfferId(),
                r.getCreatedAt().format(DateTimeFormatter.ISO_OFFSET_DATE_TIME)
        );
    }
}
