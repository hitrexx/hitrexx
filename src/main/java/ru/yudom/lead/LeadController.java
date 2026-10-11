package ru.yudom.lead;

import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/leads")
public class LeadController {

    private final LeadService leads;

    public LeadController(LeadService leads) {
        this.leads = leads;
    }

    @PostMapping
    public Map<String, String> create(@Valid @RequestBody Lead lead) {
        leads.accept(lead);
        return Map.of("message", "Спасибо! Заявка отправлена, менеджер скоро перезвонит.");
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<Map<String, String>> invalid(MethodArgumentNotValidException e) {
        String message = e.getBindingResult().getFieldErrors().stream()
                .map(f -> f.getDefaultMessage())
                .findFirst()
                .orElse("Проверьте поля формы");
        return ResponseEntity.badRequest().body(Map.of("message", message));
    }
}
