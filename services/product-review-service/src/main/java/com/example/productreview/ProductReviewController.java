package com.example.productreview;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/product-reviews")
public class ProductReviewController {

    private final List<ProductReviewDto> hardcoded = List.of(
            new ProductReviewDto(1, 1, 5, "Swietny produkt", "Jan Kowalski", null, "2026-04-01T10:00:00+00:00"),
            new ProductReviewDto(2, 1, 3, "Sredni produkt", "Anna Nowak", null, "2026-04-02T11:00:00+00:00"),
            new ProductReviewDto(3, 2, 4, "Calkiem dobry", "Piotr Wisniewski", 1, "2026-04-03T12:00:00+00:00")
    );

    @GetMapping
    public List<ProductReviewDto> index() {
        return hardcoded;
    }

    @GetMapping("/{id}")
    public ResponseEntity<ProductReviewDto> show(@PathVariable int id) {
        Optional<ProductReviewDto> review = hardcoded.stream()
                .filter(r -> r.id() == id)
                .findFirst();
        return review.map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }
}
