package com.example.productreview;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.OffsetDateTime;
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

    record CreateRequest(Integer productId, Integer rating, String comment, String authorName, Integer offerId) {}

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public ProductReviewDto create(@RequestBody CreateRequest req) {
        ProductReview review = new ProductReview();
        review.setProductId(req.productId());
        review.setRating(req.rating());
        review.setComment(req.comment());
        review.setAuthorName(req.authorName());
        review.setOfferId(req.offerId());
        review.setCreatedAt(OffsetDateTime.now());
        return ProductReviewDto.from(repository.save(review));
    }
}
