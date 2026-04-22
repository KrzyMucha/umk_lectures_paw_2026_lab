package com.example.productreview;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/product-reviews")
public class ProductReviewController {

    private final ProductReviewRepository repository;

    public ProductReviewController(ProductReviewRepository repository) {
        this.repository = repository;
    }

    @GetMapping
    public List<ProductReviewDto> index() {
        return repository.findAll().stream()
                .map(ProductReviewDto::from)
                .toList();
    }

    @GetMapping("/{id}")
    public ResponseEntity<ProductReviewDto> show(@PathVariable int id) {
        return repository.findById(id)
                .map(ProductReviewDto::from)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }
}
