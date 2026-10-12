package ru.yudom;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.nio.file.Files;
import java.nio.file.Path;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.forwardedUrl;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest(properties = "yudom.leads.file=target/test-leads.csv")
@AutoConfigureMockMvc
class YudomApplicationTests {

    @Autowired
    MockMvc mvc;

    @Test
    void homePageIsServed() throws Exception {
        mvc.perform(get("/")).andExpect(forwardedUrl("index.html"));
        mvc.perform(get("/index.html"))
                .andExpect(status().isOk())
                .andExpect(content().string(org.hamcrest.Matchers.containsString("js/app.js")));
    }

    @Test
    void projectsHaveComputedAreaAndPrice() throws Exception {
        mvc.perform(get("/api/projects"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].id").value("dom-76"))
                .andExpect(jsonPath("$[0].totalArea").value(76.5))
                .andExpect(jsonPath("$[0].minPrice").value(5030000))
                .andExpect(jsonPath("$[1].totalArea").value(125.0))
                .andExpect(jsonPath("$[1].minPrice").value(7888000));
    }

    @Test
    void unknownProjectIs404() throws Exception {
        mvc.perform(get("/api/projects/nope")).andExpect(status().isNotFound());
    }

    @Test
    void leadIsSavedToCsv() throws Exception {
        Path file = Path.of("target/test-leads.csv");
        Files.deleteIfExists(file);

        mvc.perform(post("/api/leads")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"name\":\"Иван\",\"phone\":\"+7 900 000-00-00\",\"project\":\"dom-125\",\"note\":\"участок 10 соток\"}"))
                .andExpect(status().isOk());

        assertThat(Files.readString(file)).contains("Иван", "Дом 125 м²", "участок 10 соток");
    }

    @Test
    void leadWithoutPhoneIsRejected() throws Exception {
        mvc.perform(post("/api/leads")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"name\":\"Иван\",\"phone\":\"\"}"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.message").exists());
    }
}
