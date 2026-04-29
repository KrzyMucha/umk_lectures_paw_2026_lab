package com.example.productreview;

import com.google.cloud.firestore.DocumentReference;
import com.google.cloud.firestore.DocumentSnapshot;
import com.google.cloud.firestore.Firestore;
import org.springframework.stereotype.Repository;

import java.time.OffsetDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ExecutionException;

@Repository
public class ProductReviewRepository {

    private static final String COLLECTION = "product_reviews";

    private final Firestore firestore;

    public ProductReviewRepository(Firestore firestore) {
        this.firestore = firestore;
    }

    public List<ProductReview> findAll() {
        try {
            return firestore.collection(COLLECTION).get().get()
                    .getDocuments().stream()
                    .map(this::toEntity)
                    .toList();
        } catch (InterruptedException | ExecutionException e) {
            throw new RuntimeException("Failed to fetch reviews from Firestore", e);
        }
    }

    public Optional<ProductReview> findById(String id) {
        try {
            DocumentSnapshot doc = firestore.collection(COLLECTION).document(id).get().get();
            if (!doc.exists()) return Optional.empty();
            return Optional.of(toEntity(doc));
        } catch (InterruptedException | ExecutionException e) {
            throw new RuntimeException("Failed to fetch review from Firestore", e);
        }
    }

    public ProductReview save(ProductReview review) {
        try {
            DocumentReference ref = firestore.collection(COLLECTION).document();
            ref.set(toMap(review)).get();
            review.setId(ref.getId());
            return review;
        } catch (InterruptedException | ExecutionException e) {
            throw new RuntimeException("Failed to save review to Firestore", e);
        }
    }

    private ProductReview toEntity(DocumentSnapshot doc) {
        ProductReview r = new ProductReview();
        r.setId(doc.getId());
        r.setProductId(toLong(doc, "productId"));
        r.setRating(toLong(doc, "rating"));
        r.setComment(doc.getString("comment"));
        r.setAuthorName(doc.getString("authorName"));
        r.setOfferId(toLong(doc, "offerId"));
        String createdAt = doc.getString("createdAt");
        if (createdAt != null) r.setCreatedAt(OffsetDateTime.parse(createdAt));
        return r;
    }

    private Integer toLong(DocumentSnapshot doc, String field) {
        Long val = doc.getLong(field);
        return val != null ? val.intValue() : null;
    }

    private Map<String, Object> toMap(ProductReview r) {
        Map<String, Object> map = new HashMap<>();
        map.put("productId", r.getProductId());
        map.put("rating", r.getRating());
        map.put("comment", r.getComment());
        map.put("authorName", r.getAuthorName());
        map.put("offerId", r.getOfferId());
        map.put("createdAt", r.getCreatedAt().toString());
        return map;
    }
}
