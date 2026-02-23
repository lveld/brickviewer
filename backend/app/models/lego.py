from sqlalchemy import Boolean, ForeignKey, Integer, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Color(Base):
    __tablename__ = "colors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    rgb: Mapped[str] = mapped_column(String(6), nullable=False)
    is_trans: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    elements: Mapped[list["Element"]] = relationship(back_populates="color")
    inventory_parts: Mapped[list["InventoryPart"]] = relationship(back_populates="color")


class Theme(Base):
    __tablename__ = "themes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("themes.id"), nullable=True)

    parent: Mapped["Theme | None"] = relationship(back_populates="children", remote_side="Theme.id")
    children: Mapped[list["Theme"]] = relationship(back_populates="parent")
    sets: Mapped[list["Set"]] = relationship(back_populates="theme")


class Set(Base):
    __tablename__ = "sets"

    set_num: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    theme_id: Mapped[int] = mapped_column(Integer, ForeignKey("themes.id"), nullable=False)
    num_parts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    img_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    theme: Mapped["Theme"] = relationship(back_populates="sets")
    inventories: Mapped[list["Inventory"]] = relationship(back_populates="set")


class Minifig(Base):
    __tablename__ = "minifigs"

    fig_num: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    num_parts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    img_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    inventory_minifigs: Mapped[list["InventoryMinifig"]] = relationship(back_populates="minifig")


class PartCategory(Base):
    __tablename__ = "part_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)

    parts: Mapped[list["Part"]] = relationship(back_populates="category")


class Part(Base):
    __tablename__ = "parts"

    part_num: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    part_cat_id: Mapped[int] = mapped_column(Integer, ForeignKey("part_categories.id"), nullable=False)
    part_material: Mapped[str | None] = mapped_column(String(50), nullable=True)

    category: Mapped["PartCategory"] = relationship(back_populates="parts")
    elements: Mapped[list["Element"]] = relationship(back_populates="part")
    inventory_parts: Mapped[list["InventoryPart"]] = relationship(back_populates="part")


class Element(Base):
    __tablename__ = "elements"

    element_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    part_num: Mapped[str] = mapped_column(String(20), ForeignKey("parts.part_num"), nullable=False)
    color_id: Mapped[int] = mapped_column(Integer, ForeignKey("colors.id"), nullable=False)
    design_id: Mapped[str | None] = mapped_column(String(20), nullable=True)

    part: Mapped["Part"] = relationship(back_populates="elements")
    color: Mapped["Color"] = relationship(back_populates="elements")


class PartRelationship(Base):
    __tablename__ = "part_relationships"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rel_type: Mapped[str] = mapped_column(String(1), nullable=False)  # P, R, B, M, T, A
    child_part_num: Mapped[str] = mapped_column(String(20), ForeignKey("parts.part_num"), nullable=False)
    parent_part_num: Mapped[str] = mapped_column(String(20), ForeignKey("parts.part_num"), nullable=False)


class Inventory(Base):
    __tablename__ = "inventories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    set_num: Mapped[str] = mapped_column(String(20), ForeignKey("sets.set_num"), nullable=False)

    set: Mapped["Set"] = relationship(back_populates="inventories")
    inventory_parts: Mapped[list["InventoryPart"]] = relationship(back_populates="inventory")
    inventory_minifigs: Mapped[list["InventoryMinifig"]] = relationship(back_populates="inventory")
    inventory_sets: Mapped[list["InventorySet"]] = relationship(
        back_populates="inventory", foreign_keys="InventorySet.inventory_id"
    )


class InventoryPart(Base):
    __tablename__ = "inventory_parts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    inventory_id: Mapped[int] = mapped_column(Integer, ForeignKey("inventories.id"), nullable=False)
    part_num: Mapped[str] = mapped_column(String(20), ForeignKey("parts.part_num"), nullable=False)
    color_id: Mapped[int] = mapped_column(Integer, ForeignKey("colors.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    is_spare: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    img_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    inventory: Mapped["Inventory"] = relationship(back_populates="inventory_parts")
    part: Mapped["Part"] = relationship(back_populates="inventory_parts")
    color: Mapped["Color"] = relationship(back_populates="inventory_parts")


class InventoryMinifig(Base):
    __tablename__ = "inventory_minifigs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    inventory_id: Mapped[int] = mapped_column(Integer, ForeignKey("inventories.id"), nullable=False)
    fig_num: Mapped[str] = mapped_column(String(20), ForeignKey("minifigs.fig_num"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    inventory: Mapped["Inventory"] = relationship(back_populates="inventory_minifigs")
    minifig: Mapped["Minifig"] = relationship(back_populates="inventory_minifigs")


class InventorySet(Base):
    __tablename__ = "inventory_sets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    inventory_id: Mapped[int] = mapped_column(Integer, ForeignKey("inventories.id"), nullable=False)
    set_num: Mapped[str] = mapped_column(String(20), ForeignKey("sets.set_num"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    inventory: Mapped["Inventory"] = relationship(
        back_populates="inventory_sets", foreign_keys=[inventory_id]
    )
