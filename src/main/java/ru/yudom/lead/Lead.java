package ru.yudom.lead;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

/** Заявка с сайта. */
public record Lead(
        @NotBlank(message = "Укажите имя")
        @Size(max = 100, message = "Имя слишком длинное")
        String name,

        @NotBlank(message = "Укажите телефон")
        @Pattern(regexp = "^[+0-9()\\-\\s]{6,25}$", message = "Проверьте номер телефона")
        String phone,

        @Size(max = 64)
        String project,

        @Size(max = 2000, message = "Комментарий слишком длинный")
        String note
) {}
