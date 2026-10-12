package ru.yudom.lead;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import ru.yudom.project.Project;
import ru.yudom.project.ProjectService;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.time.Duration;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Map;

/**
 * Сохраняет заявки в CSV-файл и, если настроен бот, присылает их в Telegram.
 */
@Service
public class LeadService {

    private static final Logger log = LoggerFactory.getLogger(LeadService.class);
    private static final DateTimeFormatter TIME = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    private final Path file;
    private final String botToken;
    private final String chatId;
    private final ProjectService projects;
    private final ObjectMapper mapper;
    private final HttpClient http = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(5)).build();

    public LeadService(@Value("${yudom.leads.file}") String file,
                       @Value("${yudom.telegram.bot-token}") String botToken,
                       @Value("${yudom.telegram.chat-id}") String chatId,
                       ProjectService projects,
                       ObjectMapper mapper) {
        this.file = Path.of(file);
        this.botToken = botToken;
        this.chatId = chatId;
        this.projects = projects;
        this.mapper = mapper;
    }

    public void accept(Lead lead) {
        String projectName = lead.project() == null || lead.project().isBlank()
                ? "не выбран"
                : projects.findById(lead.project()).map(Project::name).orElse(lead.project());
        String time = LocalDateTime.now().format(TIME);

        log.info("Новая заявка: {}, {}, проект: {}", lead.name(), lead.phone(), projectName);
        save(time, lead, projectName);
        notifyTelegram(time, lead, projectName);
    }

    private synchronized void save(String time, Lead lead, String projectName) {
        try {
            if (file.getParent() != null) {
                Files.createDirectories(file.getParent());
            }
            boolean isNew = Files.notExists(file);
            String line = String.join(";", csv(time), csv(lead.name()), csv(lead.phone()),
                    csv(projectName), csv(lead.note())) + "\n";
            String content = isNew ? "﻿Время;Имя;Телефон;Проект;Комментарий\n" + line : line;
            Files.writeString(file, content, StandardCharsets.UTF_8,
                    StandardOpenOption.CREATE, StandardOpenOption.APPEND);
        } catch (IOException e) {
            log.error("Не удалось записать заявку в {}", file, e);
        }
    }

    private void notifyTelegram(String time, Lead lead, String projectName) {
        if (botToken.isBlank() || chatId.isBlank()) {
            return;
        }
        String text = "Новая заявка с сайта ЮДОМ\n"
                + "Время: " + time + "\n"
                + "Имя: " + lead.name() + "\n"
                + "Телефон: " + lead.phone() + "\n"
                + "Проект: " + projectName
                + (lead.note() == null || lead.note().isBlank() ? "" : "\nКомментарий: " + lead.note());
        try {
            String body = mapper.writeValueAsString(Map.of("chat_id", chatId, "text", text));
            HttpRequest req = HttpRequest.newBuilder(URI.create("https://api.telegram.org/bot" + botToken + "/sendMessage"))
                    .timeout(Duration.ofSeconds(10))
                    .header("Content-Type", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofString(body))
                    .build();
            http.sendAsync(req, HttpResponse.BodyHandlers.discarding())
                    .thenAccept(r -> {
                        if (r.statusCode() != 200) {
                            log.warn("Telegram ответил {}", r.statusCode());
                        }
                    })
                    .exceptionally(e -> {
                        log.warn("Не удалось отправить заявку в Telegram: {}", e.getMessage());
                        return null;
                    });
        } catch (IOException e) {
            log.warn("Не удалось подготовить сообщение для Telegram", e);
        }
    }

    /** Экранирует значение для CSV (разделитель «;», как ждёт русский Excel). */
    private static String csv(String value) {
        if (value == null) {
            return "";
        }
        String v = value.replace("\r", " ").replace("\n", " ");
        // Защита от формул в Excel
        if (!v.isEmpty() && "=+-@".indexOf(v.charAt(0)) >= 0 && !v.matches("^\\+?[0-9()\\-\\s]+$")) {
            v = "'" + v;
        }
        return "\"" + v.replace("\"", "\"\"") + "\"";
    }
}
