import React from 'react';

const CategoriesSection = ({ categories }) => {
  return (
    <section className="py-16 px-4 bg-white">
      <div className="container mx-auto">
        <h2 className="text-3xl font-bold text-center mb-12">
          Explore Categories
        </h2>
        
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-7 gap-4">
          {categories.map((category, index) => (
            <div
              key={index}
              className="bg-gradient-to-br from-blue-50 to-purple-50 border border-gray-200 rounded-lg p-6 text-center hover:shadow-lg hover:scale-105 transition-all duration-300 cursor-pointer"
            >
              <h3 className="font-bold text-gray-900 text-sm mb-1">
                {category.name}
              </h3>
              <p className="text-blue-600 text-xs font-semibold">
                {category.label}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default CategoriesSection;
