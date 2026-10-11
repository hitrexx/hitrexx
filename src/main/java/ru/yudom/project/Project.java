package ru.yudom.project;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.List;

/**
 * Проект дома из каталога. Данные лежат в resources/projects.json.
 * Если {@code area} не задана, общая площадь считается как сумма комнат.
 * Цена задаётся либо одним числом {@code price} («под ключ»), либо списком {@code prices}.
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
public record Project(
        String id,
        String name,
        int floors,
        int bedrooms,
        Long price,
        List<PriceTier> prices,
        Double area,
        String totalNote,
        String desc,
        List<Spec> specs,
        Walls walls,
        List<Image> images,
        List<Room> rooms
) {
    public record PriceTier(String label, long price) {}
    public record Spec(String name, String value) {}
    public record Room(String name, double area) {}
    public record Image(String src, String alt, String cap, boolean plan) {}
    public record WallOption(String title, String text) {}
    public record Walls(String note, int base, List<WallOption> options) {}

    /** Общая площадь, округлённая до десятых. */
    @JsonProperty("totalArea")
    public double totalArea() {
        if (area != null) {
            return area;
        }
        double sum = rooms.stream().mapToDouble(Room::area).sum();
        return Math.round(sum * 10) / 10.0;
    }

    /** Цена «от»: минимальная из вариантов отделки или единственная цена. */
    @JsonProperty("minPrice")
    public long minPrice() {
        if (prices != null && !prices.isEmpty()) {
            return prices.stream().mapToLong(PriceTier::price).min().getAsLong();
        }
        return price == null ? 0 : price;
    }
}
